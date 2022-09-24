package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.Condition;
import top.kribug.deviceservice.entity.Device;
import top.kribug.deviceservice.mapper.ConditionMapper;
import top.kribug.deviceservice.service.ConditionService;

import java.util.List;

@Service
public class ConditionServiceImpl implements ConditionService {

    @Autowired
    private ConditionMapper conditionMapper;

    @Override
    public List<Condition> selectAllCondition() {
        return conditionMapper.selectAllCondition();
    }

    @Override
    public Condition selectById(Integer id) {
        return conditionMapper.selectById(id);
    }

    @Override
    public List<Condition> selectByAutomationId(Automation automation) {
        return conditionMapper.selectByAutomationId(automation);
    }

    @Override
    public List<Condition> selectByDeviceId(Device device) {
        return conditionMapper.selectByDeviceId(device);
    }

    @Override
    public boolean insert(Condition condition) {
        return conditionMapper.insert(condition);
    }

    @Override
    public boolean delete(Condition condition) {
        return conditionMapper.delete(condition);
    }

    @Override
    public boolean update(Condition condition) {
        return conditionMapper.update(condition);
    }
}
