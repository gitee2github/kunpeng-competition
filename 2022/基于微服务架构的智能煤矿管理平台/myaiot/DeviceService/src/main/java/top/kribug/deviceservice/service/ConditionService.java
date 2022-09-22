package top.kribug.deviceservice.service;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.Condition;
import top.kribug.deviceservice.entity.Device;

import java.util.List;

public interface ConditionService {

    List<Condition> selectAllCondition();

    Condition selectById(Integer id);

    List<Condition> selectByAutomationId(Automation automation);

    List<Condition> selectByDeviceId(Device Device);

    boolean insert(Condition condition);

    boolean delete(Condition condition);

    boolean update(Condition condition);
}
