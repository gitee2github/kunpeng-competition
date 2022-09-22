package top.kribug.asr;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@SpringBootApplication
@EnableFeignClients
public class AsrApplication {

    public static void main(String[] args) {
        SpringApplication.run(AsrApplication.class, args);

    }

}
