package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.deviceservice.entity.Condition;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.ConditionService;

@RestController
@RequestMapping("/device/condition")
public class ConditionController {
    
    @Autowired
    private ConditionService conditionService;
    
    @PostMapping("/")
    public Result<Boolean> add(Condition condition) {
        if (condition == null || condition.getAutomationId() == null || condition.getCompare() == null
                || condition.getValue() == null || condition.getAttributeId() == null || condition.getDeviceId() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean insert = conditionService.insert(condition);
        return new Result<>(StatusCode.SUCCESS, insert);
    }
}
