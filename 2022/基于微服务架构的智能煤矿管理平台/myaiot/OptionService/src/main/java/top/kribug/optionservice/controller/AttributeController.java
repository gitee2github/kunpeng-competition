package top.kribug.optionservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.optionservice.entity.Attribute;
import top.kribug.optionservice.service.AttributeService;

import java.util.List;

@RestController
@RequestMapping("/option")
public class AttributeController {

    @Autowired
    private AttributeService attributeService;

    @GetMapping("/attribute/getAll")
    public List<Attribute> getAllAttribute(){
        return attributeService.selectAllAttribute();
    }

    @GetMapping("/attribute/getByModelId/{id}")
    public List<Attribute> getAllAttribute(@PathVariable Integer id){
        System.out.println(id);
        return attributeService.selectByModelId(id);
    }
}
