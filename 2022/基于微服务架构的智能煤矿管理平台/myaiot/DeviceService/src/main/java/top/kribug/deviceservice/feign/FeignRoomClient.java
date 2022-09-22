package top.kribug.deviceservice.feign;

import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import top.kribug.deviceservice.entity.Room;

@FeignClient(value = "ROOMSERVICE")
public interface FeignRoomClient {
    @GetMapping("/room/getUserAllRoomFeign/{id}")
    public String getUserAllRoom(@PathVariable(name = "id") Integer id);

    @GetMapping("/room/feign/{id}")
    public Room getByIdFeign(@PathVariable(name = "id") Integer id);
}
