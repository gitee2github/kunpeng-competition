package top.kribug.deviceservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.deviceservice.entity.Model;
import top.kribug.deviceservice.mapper.ModelMapper;
import top.kribug.deviceservice.service.ModelService;

import java.util.List;

@Service
public class ModelServiceImpl implements ModelService {

    @Autowired
    private ModelMapper modelMapper;
    @Override
    public List<Model> selectAllModel() {
        return modelMapper.selectAllModel();
    }

    @Override
    public Model selectById(Integer id) {
        return modelMapper.selectById(id);
    }

    @Override
    public boolean insert(Model model) {
        return modelMapper.insert(model);
    }

    @Override
    public boolean delete(Model model) {
        return modelMapper.delete(model);
    }

    @Override
    public boolean update(Model model) {
        return modelMapper.update(model);
    }
}
