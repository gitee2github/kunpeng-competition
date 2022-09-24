package top.kribug.attributeservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.attributeservice.entity.Attribute;
import top.kribug.attributeservice.mapper.AttributeMapper;
import top.kribug.attributeservice.service.AttributeService;

import java.util.List;

@Service
public class AttributeServiceImpl implements AttributeService {
    @Autowired
    private AttributeMapper attributeMapper;

    @Override
    public List<Attribute> selectAllAttribute() {
        return attributeMapper.selectAllAttribute();
    }

    @Override
    public List<Attribute> selectByModelId(Integer modelId) {
        return attributeMapper.selectByModelId(modelId);
    }

    @Override
    public Attribute selectById(Integer id) {
        return attributeMapper.selectById(id);
    }

    @Override
    public boolean insert(Attribute attribute) {
        return attributeMapper.insert(attribute);
    }

    @Override
    public boolean delete(Attribute attribute) {
        return attributeMapper.delete(attribute);
    }

}
