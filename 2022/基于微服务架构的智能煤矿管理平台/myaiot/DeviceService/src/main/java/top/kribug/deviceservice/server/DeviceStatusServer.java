package top.kribug.deviceservice.server;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.DeviceService;

@Component
public class DeviceStatusServer {


    @Autowired
    private DeviceService deviceService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    public Device getDeviceById(Integer id){
        if(id == null){
            return null;
        }
        Device device = deviceService.selectById(id);
        if(device == null){
            return null;
        }
        String s = redisTemplate.opsForValue().get("device:" + device.getId());
        if(s != null){
            device.setInLineState(1);
            device.setJsonStatusInfo(s);
        }else{
            device.setInLineState(0);
        }

        return device;
    }
}
