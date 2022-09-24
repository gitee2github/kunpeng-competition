package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.AutomationService;

import java.util.List;

@RestController
@RequestMapping("/device/automation")
public class AutomationController {

    @Autowired
    private AutomationService automationService;

    @GetMapping("/getAll")
    public Result<List<Automation>> getAll(User user) {
        if (user == null || user.getId() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        return new Result<>(StatusCode.SUCCESS, automationService.selectByUserId(user));
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Integer id) {
        if (id == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Automation automation = new Automation();
        automation.setId(id);
        boolean delete = automationService.delete(automation);
        return new Result<>(StatusCode.SUCCESS, delete);
    }

    @PutMapping("/updateStatus")
    public Result<Boolean> updateStatus(Automation automation) {
        if (automation == null || automation.getId() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        if (automation.getStatus() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean b = automationService.updateStatus(automation);
        return new Result<>(StatusCode.SUCCESS, b);
    }

    @PutMapping("/")
    public Result<Boolean> update(Automation automation) {
        if (automation == null || automation.getId() == null || automation.getUserId() == null || automation.getTitle() == null
                || automation.getAndCondition() == null || automation.getStatus() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean b = automationService.update(automation);
        return new Result<>(StatusCode.SUCCESS, b);
    }

    @PostMapping("/")
    public Result<Boolean> add(Automation automation) {
        if (automation == null || automation.getUserId() == null || automation.getTitle() == null
        || automation.getAndCondition() == null || automation.getStatus() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean insert = automationService.insert(automation);
        return new Result<>(StatusCode.SUCCESS, insert);
    }

    @PostMapping("/addGetId")
    public Result<Integer> addGetId(Automation automation) {
        if (automation == null || automation.getUserId() == null || automation.getTitle() == null
                || automation.getAndCondition() == null || automation.getStatus() == null) {
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean insert = automationService.insert(automation);
        return new Result<>(StatusCode.SUCCESS, automation.getId());
    }


}