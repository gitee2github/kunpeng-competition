package top.kribug.kribuglight;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.FeignClient;

@SpringBootApplication
@FeignClient
public class KribugLightApplication {

    public static void main(String[] args) {
        SpringApplication.run(KribugLightApplication.class, args);
    }

}
