package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Automation;
import top.kribug.deviceservice.entity.User;
import top.kribug.deviceservice.mapper.AutomationMapper;
import top.kribug.deviceservice.service.AutomationService;

import java.util.List;

@Service
public class AutomationServiceImpl implements AutomationService {

    @Autowired
    private AutomationMapper automationMapper;

    @Override
    public List<Automation> selectAllAutomation() {
        return automationMapper.selectAllAutomation();
    }

    @Override
    public Automation selectById(Integer id) {
        return automationMapper.selectById(id);
    }

    @Override
    public List<Automation> selectByUserId(User user) {
        return automationMapper.selectByUserId(user);
    }

    @Override
    public boolean insert(Automation automation) {
        return automationMapper.insert(automation);
    }

    @Override
    public boolean delete(Automation automation) {
        return automationMapper.delete(automation);
    }

    @Override
    public boolean update(Automation automation) {
        return automationMapper.update(automation);
    }

    @Override
    public boolean updateStatus(Automation automation) {
        return automationMapper.updateStatus(automation);
    }

    @Override
    public boolean updateTitle(Automation automation) {
        return automationMapper.updateTitle(automation);
    }
}
