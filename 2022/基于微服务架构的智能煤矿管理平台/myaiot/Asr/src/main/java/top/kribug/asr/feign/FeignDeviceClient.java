package top.kribug.asr.feign;

import feign.Param;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import top.kribug.asr.entity.User;
import top.kribug.asr.result.Result;
import top.kribug.asr.result.StatusCode;

import javax.servlet.http.HttpSession;

@FeignClient(value = "DEVICESERVICE")
public interface FeignDeviceClient {

    @PostMapping("/device/asr")
    public String asr(@Param("attr") String attr);
}