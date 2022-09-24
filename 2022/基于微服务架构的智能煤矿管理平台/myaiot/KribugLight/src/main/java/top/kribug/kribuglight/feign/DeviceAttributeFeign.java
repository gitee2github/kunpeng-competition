package top.kribug.kribuglight.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;

@FeignClient("DeviceService")
public interface DeviceAttributeFeign {
    @GetMapping("/device/attribute/MY_SWITCH/{id}")
    public void s();
}
