package top.kribug.deviceservice.server;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.client.RestTemplate;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.Model;
import top.kribug.deviceservice.entity.Room;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.feign.FeignRoomClient;
import top.kribug.deviceservice.feign.FeignUserClient;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.service.DeviceService;
import top.kribug.deviceservice.service.ModelService;

import java.lang.reflect.Type;
import java.util.*;

@Service
public class AsrServer {

    @Data
    private class Option{
        String key;
        String value;
        public Option(String key, String value){
            this.key = key;
            this.value = value;
        }
    }

    @Autowired
    private FeignRoomClient roomClient;

    @Autowired
    private FeignUserClient userClient;

    @Autowired
    private ModelService modelService;

    @Autowired
    private DeviceService deviceService;

    @Autowired
    ObjectMapper mapper;

    @Autowired
    RestTemplate restTemplate;


    private Map<String, Option> OPTION;
    {
        OPTION = new HashMap<>();
        Option my_switch_open = new Option("MY_SWITCH", "1");
        OPTION.put("打开", my_switch_open);
        OPTION.put("开启", my_switch_open);
        OPTION.put("开", my_switch_open);
        OPTION.put("启动", my_switch_open);
    }
    {
        Option my_switch_close = new Option("MY_SWITCH", "-1");
        OPTION.put("关闭", my_switch_close);
        OPTION.put("关了", my_switch_close);
        OPTION.put("关", my_switch_close);
    }

    private List<Model> ModelList;
    private List<Device> DeviceList;
    private List<Room> RoomList;
    private User user;//当前用户

    public void start(Integer id){
        if(id == null){
            System.out.println("id == null");
            return;
        }
        user = userClient.getById(id);
        String userAllRoomJson = roomClient.getUserAllRoom(user.getId());
        try {
            RoomList = mapper.readValue(userAllRoomJson, new TypeReference<List<Room>>(){});
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        ModelList = modelService.selectAllModel();
        DeviceList = deviceService.selectByUserId(user);

    }

    public String run(String speak){
        System.out.println(user);
        System.out.println(ModelList);
        System.out.println(DeviceList);
        System.out.println(RoomList);
        List<Device> optionDevice = new ArrayList<>();
        Option option = null;
        Room optionRoom = null;
        for (Device device : DeviceList) {
            if(speak.contains(device.getTitle())){
                optionDevice.add(device);
            }
        }
        System.out.println("操作设备是："+optionDevice);

        for (Map.Entry<String, Option> stringOptionEntry : OPTION.entrySet()) {
            if(speak.contains(stringOptionEntry.getKey())){
                option = stringOptionEntry.getValue();
                break;
            }
        }

        System.out.println("操作是："+option);

        for (Room room : RoomList) {
            if(speak.contains(room.getTitle())){
                optionRoom = room;
                break;
            }
        }
        System.out.println("操作的房间是："+optionRoom);

        if(optionRoom != null){
            for(int i = 0 ; i < optionDevice.size() ; i++){
                if(!Objects.equals(optionDevice.get(i).getRoomId(), optionRoom.getId())){
                    optionDevice.remove(i);
                    i--;
                }
            }

        }

        if(optionDevice.size() > 0 && option != null){
            if(optionDevice.size() == 1){
                DataContainer.addData(optionDevice.get(0).getId()+"", option.getKey(), option.getValue());
                //请求地址
                String url = "http://112.74.34.69/device/option?id="+optionDevice.get(0).getId()+"&value=" +
                        option.getValue() + "&key=" + option.getKey();
                restTemplate.postForEntity(url, new LinkedMultiValueMap(), String.class);
                return "先帮你操作了";
            }
            for (Device device : optionDevice) {
                DataContainer.addData(device.getId()+"", option.getKey(), option.getValue());
                //请求地址
                String url = "http://112.74.34.69/device/option?id="+device.getId()+"&value=" +
                        option.getValue() + "&key=" + option.getKey();
                restTemplate.postForEntity(url, new LinkedMultiValueMap(), String.class);
            }
            return "共有"+optionDevice.size()+"同名设备，全部帮你操作了";
        }

        return "暂不支持该操作";
    }

}
