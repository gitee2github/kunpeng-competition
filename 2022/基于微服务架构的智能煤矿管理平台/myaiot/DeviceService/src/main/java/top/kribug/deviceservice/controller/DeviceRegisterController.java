package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.deviceservice.service.DeviceService;
import top.kribug.deviceservice.entity.Device;

@RestController
@RequestMapping("/device")
@CrossOrigin
public class DeviceRegisterController {

    /*
    * 设备注册服务
    * 返回1代表成功注册
    * */
    @Autowired
    private DeviceService deviceService;
    @GetMapping("/register")
    public String register(Device device){
        if(device == null){
            return "data0";
        }
        if(deviceService.bind(device)){
            return "data1";
        }
        return "data-1";
    }
}
