package top.kribug.attributeservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.attributeservice.entity.Attribute;
import top.kribug.attributeservice.service.AttributeService;

import java.util.List;

@RestController
@RequestMapping("/attribute")
public class AttributeController {

    @Autowired
    private AttributeService attributeService;

    @GetMapping("/getAll")
    public List<Attribute> getAllAttribute(){
        return attributeService.selectAllAttribute();
    }

    @GetMapping("/getByModelId/{id}")
    public List<Attribute> getAllAttribute(@PathVariable Integer id){
        System.out.println(id);
        return attributeService.selectByModelId(id);
    }
}
