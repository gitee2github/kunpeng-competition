package top.kribug.userservice.service;


import top.kribug.userservice.entity.User;

import java.util.List;

public interface UserService {
    boolean register(User user);
    User login(User user);
    boolean delete(User user);
    boolean update(User user);
    boolean logout();
    List<User> selectAll();
    User selectById(Integer id);
    User selectByUsername(String username);
    User selectByPhone(String Phone);
}
