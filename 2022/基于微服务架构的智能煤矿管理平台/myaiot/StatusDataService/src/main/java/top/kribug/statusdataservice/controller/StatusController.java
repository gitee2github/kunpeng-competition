package top.kribug.statusdataservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.statusdataservice.entity.Status;
import top.kribug.statusdataservice.service.StatusService;

@RestController
@RequestMapping("/status")
public class StatusController {

    @Autowired
    private StatusService statusService;

    @PostMapping("/")
    public Boolean save(Status status){
        Boolean res = statusService.insert(status);
        return res;
    }
}
