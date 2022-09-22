package top.kribug.deviceservice.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import top.kribug.deviceservice.entity.User;


@FeignClient(value = "USERSERVICE")
public interface FeignUserClient {
    @GetMapping("/user/{id}")
    public User getById(@PathVariable("id") Integer id);
}
