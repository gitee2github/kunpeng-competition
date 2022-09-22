package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Option;
import top.kribug.deviceservice.mapper.OptionMapper;
import top.kribug.deviceservice.service.OptionService;

import java.util.List;

@Service
public class OptionServiceImpl implements OptionService {
    @Autowired
    private OptionMapper optionMapper;

    @Override
    public List<Option> selectAllOption() {
        return optionMapper.selectAllOption();
    }

    @Override
    public List<Option> selectByModelId(Integer modelId) {
        return optionMapper.selectByModelId(modelId);
    }

    @Override
    public Option selectById(Integer id) {
        return optionMapper.selectById(id);
    }

    @Override
    public boolean insert(Option option) {
        return optionMapper.insert(option);
    }

    @Override
    public boolean delete(Option option) {
        return optionMapper.delete(option);
    }

}
