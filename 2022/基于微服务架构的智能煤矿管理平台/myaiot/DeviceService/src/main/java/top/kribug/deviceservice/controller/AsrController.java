package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.feign.FeignUserClient;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.server.AsrServer;

import javax.servlet.http.HttpSession;

@CrossOrigin
@RestController
@RequestMapping("/device")
public class AsrController {

    @Autowired
    private AsrServer asrServer;

    @PostMapping("/asr")
    public String asr(@RequestBody String attr){
//        User currentUser = userClient.getCurrentUser(session);
        if(attr == null){
            System.out.println("参数为空！！！！！！");
            return "我什么都没听到";
        }
        asrServer.start(10013);
        return asrServer.run(attr);
    }
}
