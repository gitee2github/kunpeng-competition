package top.kribug.userservice;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import top.kribug.userservice.entity.User;
import top.kribug.userservice.mapper.UserMapper;

import java.util.List;

@SpringBootTest
class UserServerApplicationTests {

    @Test
    void contextLoads() {
    }

    @Autowired
    UserMapper userMapper;
    @Test
    void s1() {
        List<User> users = userMapper.selectAllUser();
        System.out.println(users);
    }
}
