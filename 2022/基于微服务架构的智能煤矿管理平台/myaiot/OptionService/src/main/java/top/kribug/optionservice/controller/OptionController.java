package top.kribug.optionservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import top.kribug.optionservice.entity.Option;
import top.kribug.optionservice.service.OptionService;

import java.util.List;

@RestController
@RequestMapping("/option")
public class OptionController {

    @Autowired
    private OptionService optionService;

    @GetMapping("/getAll")
    public List<Option> getAllOption(){
        return optionService.selectAllOption();
    }

    @GetMapping("/getByModelId/{id}")
    public List<Option> getAllOption(@PathVariable Integer id){
        System.out.println(id);
        return optionService.selectByModelId(id);
    }
}
