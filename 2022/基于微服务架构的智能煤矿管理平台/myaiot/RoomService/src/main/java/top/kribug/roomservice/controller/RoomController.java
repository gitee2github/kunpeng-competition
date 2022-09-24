package top.kribug.roomservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import top.kribug.roomservice.entity.Room;
import top.kribug.roomservice.result.Result;
import top.kribug.roomservice.result.StatusCode;
import top.kribug.roomservice.service.RoomService;

import java.util.List;

@RestController
@RequestMapping("/room")
@CrossOrigin
public class RoomController {

    @Autowired
    private RoomService roomService;

    @GetMapping("/getUserAllRoom/{id}")
    public Result<List<Room>> getUserAllRoom(@PathVariable Integer id){
        List<Room> rooms = roomService.selectUserAllRoom(id);
        return new Result<>(StatusCode.SUCCESS, rooms);
    }

    @GetMapping("/getUserAllRoomFeign/{id}")
    public List<Room> getUserAllRoomFeign(@PathVariable Integer id){
        List<Room> rooms = roomService.selectUserAllRoom(id);
        return rooms;
    }

    @GetMapping("/{id}")
    public Result<Room> getById(@PathVariable Integer id){
        if(id == null){
            Room room = new Room();
            room.setTitle("默认房间");
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, room);
        }
        Room room = roomService.selectById(id);
        return new Result<>(StatusCode.SUCCESS, room);
    }

    @GetMapping("/feign/{id}")
    public Room getByIdFeign(@PathVariable Integer id){
        if(id == null){
            Room room = new Room();
            room.setTitle("默认房间");
            return room;
        }
        Room room = roomService.selectById(id);
        return room;
    }


    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Integer id){
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean res = false;
        Room room = new Room();
        room.setId(id);
        res = roomService.delete(room);
        if(res){
            return new Result<>(StatusCode.SUCCESS, res);
        }
        return new Result<>(StatusCode.SQL_ERROR, false);
    }

    @PostMapping("/")
    public Result<Room> add(Room room){
        if(room == null || room.getTitle() == null || room.getUserId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        boolean res = false;
        res = roomService.insert(room);
        if(res){
            return new Result<>(StatusCode.SUCCESS, room);
        }
        return new Result<>(StatusCode.SQL_ERROR, null);
    }

    @PutMapping("/")
    public Result<Boolean> update(Room room){
        if(room == null || room.getId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean res = false;
        res = roomService.update(room);
        return new Result<>(StatusCode.SUCCESS, res);
    }
}
