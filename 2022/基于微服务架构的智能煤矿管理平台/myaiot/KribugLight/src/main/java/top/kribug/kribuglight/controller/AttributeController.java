package top.kribug.kribuglight.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/attribute")
public class AttributeController {

    @GetMapping("MY_SWITCH/{id}")
    public String getMY_SWITCH(@PathVariable Integer id){
        return id+"";
    }
}
