package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.deviceservice.entity.Action;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.ActionService;

@RestController
@RequestMapping("/device/action")
public class ActionController {

    @Autowired
    private ActionService actionService;

    @PostMapping("/")
    public Result<Boolean> add(Action action) {
        if (action == null || action.getAutomationId() == null
                || action.getOptionId() == null || action.getDeviceId() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean insert = actionService.insert(action);
        return new Result<>(StatusCode.SUCCESS, insert);
    }
}
