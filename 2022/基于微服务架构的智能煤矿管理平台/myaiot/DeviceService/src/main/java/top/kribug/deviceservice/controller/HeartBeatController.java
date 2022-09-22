package top.kribug.deviceservice.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.Model;
import top.kribug.deviceservice.entity.Statistics;
import top.kribug.deviceservice.entity.Status;
import top.kribug.deviceservice.server.AutomationServer;
import top.kribug.deviceservice.server.DataContainer;
import top.kribug.deviceservice.server.HeartBeatServer;
import top.kribug.deviceservice.service.DeviceService;
import top.kribug.deviceservice.service.StatisticsService;
import top.kribug.deviceservice.service.StatusService;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/device")
@CrossOrigin
public class HeartBeatController {

    @Autowired
    private HeartBeatServer heartBeatServer;

    @Autowired
    private DataContainer dataContainer;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AutomationServer automationServer;

    @Autowired
    private StatusService statusService;

    @Autowired
    private StatisticsService statisticsService;

    @Autowired
    private DeviceService deviceService;


    @GetMapping("/beat")
    public HashMap<String, String> heartBeat(@RequestParam HashMap<String, String> data){

        if(!data.containsKey("id") || !data.containsKey("password")){
            return null;
        }
        if(!heartBeatServer.checkIdAndPassword(data.get("id"), data.get("password"))){
            return null;
        }
        Set<Map.Entry<String, String>> entries = data.entrySet();
        String id = data.get("id");
        if(Boolean.FALSE.equals(redisTemplate.hasKey("report:" + id))){
            for (Map.Entry<String, String> entry : entries) {
                if("id".equals(entry.getKey()) || "password".equals(entry.getKey())){
                    continue;
                }
                String key = entry.getKey();
                String value = entry.getValue();
                Status status = new Status();
                status.setKey(key);
                status.setValue(value);
                status.setDeviceId(Integer.valueOf(id));
                Device device = deviceService.selectById(Integer.valueOf(id));
                if(device.getModelId() == 13){//水位传感器
                    Statistics statistics = new Statistics();
                    Date date = new Date();
                    statistics.setName(date.getMinutes() + ":" + date.getSeconds());
                    statistics.setIndicative_value1(value);
                    Boolean insert = statisticsService.insert(statistics);
                }
                redisTemplate.opsForValue().set("report:"+id, "", 20, TimeUnit.SECONDS);
            }
        }

        String dataJson = "";
        try {
            dataJson = objectMapper.writeValueAsString(data);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        redisTemplate.opsForValue().set("device:"+data.get("id"), dataJson, 5, TimeUnit.SECONDS);
        HashMap<String, String> res = new HashMap<>();
        if(dataContainer.hasId(data.get("id"))){
            res = dataContainer.getData(data.get("id"));
            dataContainer.clearId(data.get("id"));
        }
        if(res == null){
            res =  new HashMap<>();
        }

        //获取redis中的操作
        if(Boolean.TRUE.equals(redisTemplate.hasKey("optionRemote:" + data.get("id")))){
            String option = redisTemplate.opsForValue().get("optionRemote:" + data.get("id"));
            assert option != null;
            String optionKey = option.substring(0, option.indexOf(':'));
            String optionValue = option.substring(option.indexOf(':') + 1);
            System.out.println("optionRemote="+optionKey+":" +optionValue);
            res.put(optionKey, optionValue);
            redisTemplate.delete("optionRemote:" + data.get("id"));
        }

        automationServer.dataChange(Integer.valueOf(data.get("id")));
        return res;
    }
}
