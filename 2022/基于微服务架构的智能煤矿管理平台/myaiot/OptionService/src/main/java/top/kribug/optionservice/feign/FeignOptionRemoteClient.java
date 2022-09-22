package top.kribug.optionservice.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import top.kribug.optionservice.result.Result;

@Service
@FeignClient(value = "DeviceService")
public interface FeignOptionRemoteClient {
    @PostMapping("/device/optionRemote?id={id}&key={key}&value={value}")
    public void optionRemote(@PathVariable("id") Integer id, @PathVariable("key") String key,@PathVariable("value") String value);
}
