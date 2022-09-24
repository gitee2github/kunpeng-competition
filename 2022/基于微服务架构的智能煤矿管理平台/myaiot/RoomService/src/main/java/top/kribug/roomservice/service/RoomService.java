package top.kribug.roomservice.service;

import top.kribug.roomservice.entity.Room;

import java.util.List;

public interface RoomService {
    List<Room> selectUserAllRoom(Integer UserId);

    Room selectById(Integer id);

    boolean insert(Room room);

    boolean delete(Room room);

    boolean update(Room room);
}
