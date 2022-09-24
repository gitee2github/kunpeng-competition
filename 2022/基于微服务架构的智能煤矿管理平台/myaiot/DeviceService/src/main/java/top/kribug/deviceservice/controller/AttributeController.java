package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.Attribute;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.AttributeService;
import top.kribug.deviceservice.service.DeviceService;

import java.util.Date;
import java.util.List;

@RestController
@RequestMapping("/device")
@CrossOrigin
public class AttributeController {

    @Autowired
    private DeviceService deviceService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;
/*
    @GetMapping("/MY_SWITCH/{id}")
    public Device getDeviceById(@PathVariable Integer id){
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
            return null;
        }

        return device;
    }*/

    @Autowired
    private AttributeService attributeService;

    @GetMapping("/attribute/getAll")
    public Result<List<Attribute>> getAllAttribute(){
        return new Result<>(StatusCode.SUCCESS, attributeService.selectAllAttribute());
    }
    @GetMapping("/attribute/getByModelId/{id}")
    public Result<List<Attribute>> getByModelId(@PathVariable Integer id) {
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        return new Result<>(StatusCode.SUCCESS, attributeService.selectByModelId(id));
    }

    @GetMapping("/attribute/getByDeviceId/{id}")
    public Result<List<Attribute>> getByDeviceId(@PathVariable Integer id) {
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Device device = deviceService.selectById(id);
        return getByModelId(device.getModelId());
    }

}
