package top.kribug.optionservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.optionservice.feign.FeignOptionRemoteClient;
import top.kribug.optionservice.result.Result;
import top.kribug.optionservice.result.StatusCode;

@RestController
@RequestMapping("/option")
public class ExecuteOption {

    @Autowired
    private FeignOptionRemoteClient feignOptionRemoteClient;

    @PostMapping("/execute/optionRemoteOne")
    public void optionRemoteOne(Integer id, String key, String value){
        if(id == null ||  key == null || key.equals("")){
            return;
        }
        feignOptionRemoteClient.optionRemote(id, key, value);
    }
}
