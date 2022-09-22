package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.DeviceService;

import java.util.Date;
import java.util.List;
import java.util.Random;

@RestController
@RequestMapping("/device")
@CrossOrigin
public class DeviceController {

    @Autowired
    private DeviceService deviceService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @GetMapping("/getDeviceByUser")
    public Result<List<Device>> getDeviceByUser(User user){
        if(user == null || user.getId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        List<Device> devices = deviceService.selectByUserId(user);

        return new Result<List<Device>>(StatusCode.SUCCESS, devices);
    }

    @GetMapping("/{id}")
    public Result<Device> getDeviceById(@PathVariable Integer id){
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Device device = deviceService.selectById(id);
        if(device == null){
            return new Result<Device>(StatusCode.ID_ERROR, null);
        }
        String s = redisTemplate.opsForValue().get("device:" + device.getId());
        if(s != null){
            device.setInLineState(1);
            device.setJsonStatusInfo(s);
        }else{
            device.setInLineState(0);
        }

        return new Result<Device>(StatusCode.SUCCESS, device);
    }

    @PostMapping("/")
    public Result<Device> addDevice(Device device){
        if(device == null || device.getUserId() == null || device.getModelId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        device.setAddTime(new Date());
        String pass = (int)(Math.random()*1000000) + "";
        device.setPassword(pass);
        boolean res = deviceService.insert(device);
        if(res){
            return new Result<>(StatusCode.SUCCESS, device);
        }else {
            return new Result<>(StatusCode.SQL_ERROR, null);
        }
    }

    @DeleteMapping("/{id}")
    public Result<Device> addDevice(@PathVariable Integer id){
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Device device = new Device();
        device.setId(id);
        boolean res = deviceService.delete(device);
        if(res){
            return new Result<>(StatusCode.SUCCESS, device);
        }else {
            return new Result<>(StatusCode.SQL_ERROR, null);
        }
    }

    @PutMapping("/updateTitle")
    public Result<Boolean> updateTitle(Device device){
        if(device == null || device.getId() == null || device.getTitle() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean res = deviceService.updateTitle(device);
        if(res){
            return new Result<>(StatusCode.SUCCESS, true);
        }else {
            return new Result<>(StatusCode.SQL_ERROR, false);
        }
    }

    @PutMapping("/updateRoom")
    public Result<Boolean> updateRoom(Device device){
        if(device == null || device.getId() == null || device.getRoomId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean res = deviceService.updateRoom(device);
        if(res){
            return new Result<>(StatusCode.SUCCESS, true);
        }else {
            return new Result<>(StatusCode.SQL_ERROR, false);
        }
    }

}
