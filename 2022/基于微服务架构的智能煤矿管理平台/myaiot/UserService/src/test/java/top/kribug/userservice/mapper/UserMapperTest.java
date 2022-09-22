package top.kribug.userservice.mapper;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import top.kribug.userservice.entity.User;


import java.util.Date;

@SpringBootTest
public class UserMapperTest {

    @Autowired
    UserMapper userMapper;
    @Test
    public void insertOneTest(){
        User user = new User();
        user.setEmail("131455555@qq.com");
        user.setAddTime(new Date());
        user.setHeadUrl("http://12312321.png");
        user.setUsername("lzy");
        user.setPassword("lxlzy");
        user.setName("刘兆颖");
        user.setPhone("18798590200");
        boolean b = userMapper.insert(user);
        System.out.println(b);
        System.out.println(user);
    }
}
