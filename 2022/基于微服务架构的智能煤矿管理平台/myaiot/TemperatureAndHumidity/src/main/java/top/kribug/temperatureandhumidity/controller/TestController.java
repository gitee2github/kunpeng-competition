package top.kribug.temperatureandhumidity.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/TemperatureAndHumidity")
public class TestController {

    @GetMapping("/a")
    public String a(){
        return "hello";
    }
}
