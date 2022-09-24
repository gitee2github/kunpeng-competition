package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Action;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.mapper.ActionMapper;
import top.kribug.deviceservice.service.ActionService;

import java.util.List;

@Service
public class ActionServiceImpl implements ActionService {
    @Autowired
    private ActionMapper actionMapper;

    @Override
    public List<Action> selectAllAction() {
        return actionMapper.selectAllAction();
    }

    @Override
    public Action selectById(Integer id) {
        return actionMapper.selectById(id);
    }

    @Override
    public List<Action> selectByAutomationId(Automation automation) {
        return actionMapper.selectByAutomationId(automation);
    }

    @Override
    public boolean insert(Action action) {
        return actionMapper.insert(action);
    }

    @Override
    public boolean delete(Action action) {
        return actionMapper.delete(action);
    }

    @Override
    public boolean update(Action action) {
        return actionMapper.update(action);
    }
}
