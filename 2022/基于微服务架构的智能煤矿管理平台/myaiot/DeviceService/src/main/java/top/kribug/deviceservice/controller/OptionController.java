package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;

import top.kribug.deviceservice.entity.Attribute;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.Option;
import top.kribug.deviceservice.server.AutomationServer;
import top.kribug.deviceservice.server.DataContainer;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.DeviceService;
import top.kribug.deviceservice.service.OptionService;

import java.util.List;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/device")
@CrossOrigin
public class OptionController {

    @Autowired
    private DataContainer dataContainer;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Autowired
    private OptionService optionService;

    @Autowired
    private AutomationServer automationServer;

    @Autowired
    private DeviceService deviceService;

    @CrossOrigin
    @PostMapping("/option")
    public Result<String> option(String id, String key, String value){
        if(id == null || id.equals("") || key == null || key.equals("")){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        dataContainer.addData(id, key, value);
        automationServer.dataChange(Integer.valueOf(id));
        return new Result<>(StatusCode.SUCCESS, null);
//        return optionRemote(id, key, value);
    }

    @CrossOrigin
    @PostMapping("/optionRemote")
    public Result<String> optionRemote(String id, String key, String value){
        if(id == null || id.equals("") || key == null || key.equals("")){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        redisTemplate.opsForValue().set("optionRemote:" + id, key+":"+value, 10, TimeUnit.SECONDS);
        String deviceStatusInfoJson = redisTemplate.opsForValue().get("device:" + id);
        if(deviceStatusInfoJson == null || deviceStatusInfoJson.length() == 0){
            return new Result<>(StatusCode.ID_ERROR, "设备不在线！");
        }
//        String newDeviceStatusInfoJson = AutomationServer.replaceValueInJsonByKey(deviceStatusInfoJson, key, value);
//        redisTemplate.opsForValue().set("device:" + id, newDeviceStatusInfoJson, 5, TimeUnit.SECONDS);
//        automationServer.dataChange(Integer.valueOf(id));
        return new Result<>(StatusCode.SUCCESS, null);
    }

    @GetMapping("/getByModelId/{id}")
    public List<Option> getAllOption(@PathVariable Integer id){
        System.out.println(id);
        return optionService.selectByModelId(id);
    }

    @GetMapping("/option/getAll")
    public Result<List<Option>> getAllOption(){
        return new Result<>(StatusCode.SUCCESS, optionService.selectAllOption());
    }
    @GetMapping("/option/getByModelId/{id}")
    public Result<List<Option>> getByModelId(@PathVariable Integer id) {
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        return new Result<>(StatusCode.SUCCESS, optionService.selectByModelId(id));
    }

    @GetMapping("/option/getByDeviceId/{id}")
    public Result<List<Option>> getByDeviceId(@PathVariable Integer id) {
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Device device = deviceService.selectById(id);
        if(device == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        return getByModelId(device.getModelId());
    }
}
