package top.kribug.roomservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.roomservice.mapper.RoomMapper;
import top.kribug.roomservice.service.RoomService;
import top.kribug.roomservice.entity.Room;

import java.util.List;

@Service
public class RoomServiceImpl implements RoomService {

    @Autowired
    private RoomMapper roomMapper;

    @Override
    public List<Room> selectUserAllRoom(Integer userId) {
        return roomMapper.selectUserAllRoom(userId);
    }

    @Override
    public Room selectById(Integer id) {
        return roomMapper.selectById(id);
    }

    @Override
    public boolean insert(Room room) {
        return roomMapper.insert(room);
    }

    @Override
    public boolean delete(Room room) {
        return roomMapper.delete(room);
    }

    @Override
    public boolean update(Room room) {
        return roomMapper.update(room);
    }
}
