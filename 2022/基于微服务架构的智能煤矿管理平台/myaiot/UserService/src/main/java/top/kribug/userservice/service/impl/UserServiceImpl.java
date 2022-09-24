package top.kribug.userservice.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import top.kribug.userservice.entity.User;
import top.kribug.userservice.mapper.UserMapper;
import top.kribug.userservice.service.UserService;

import java.util.Date;
import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;


    @Override
    public boolean register(User user) {
        //用户名查重
        if(selectByUsername(user.getUsername()) != null){
            return false;
        }
        if ((user.getState() == null) || (user.getState() != 0 && user.getState() != 1)){
            user.setState(1);
        }
        user.setAddTime(new Date());
        user.setIsAdmin(0);
        return userMapper.insert(user);
    }

    @Override
    public User login(User user) {
        return userMapper.selectByUsernameAndPassword(user);
    }

    @Override
    public boolean delete(User user) {
        return userMapper.delete(user);
    }

    @Override
    public boolean update(User user) {
        User user1 = selectById(user.getId());
        if(user.getUsername() == null){
            user.setUsername(user1.getUsername());
        }
        if(user.getPhone() == null){
            user.setPhone(user1.getPhone());
        }
        if(user.getState() == null){
            user.setState(user1.getState());
        }
        if(user.getEmail() == null){
            user.setEmail(user1.getEmail());
        }
        if(user.getName() == null){
            user.setName(user1.getName());
        }
        if(user.getPassword() == null){
            user.setPassword(user1.getPassword());
        }
        if(user.getHeadUrl() == null){
            user.setHeadUrl(user1.getHeadUrl());
        }
        if(user.getIsAdmin() == null){
            user.setIsAdmin(user1.getIsAdmin());
        }
        return userMapper.update(user);
    }

    @Override
    public boolean logout() {
        return false;
    }

    @Override
    public List<User> selectAll() {
        return userMapper.selectAllUser();
    }

    @Override
    public User selectById(Integer id) {
        return userMapper.selectById(id);
    }

    @Override
    public User selectByUsername(String username) {
        return userMapper.selectByUsername(username);
    }

    @Override
    public User selectByPhone(String phone) {
        return userMapper.selectByPhone(phone);
    }

}
