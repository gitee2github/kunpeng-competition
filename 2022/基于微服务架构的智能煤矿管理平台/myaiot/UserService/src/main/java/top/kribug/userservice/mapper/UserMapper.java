package top.kribug.userservice.mapper;

import org.apache.ibatis.annotations.*;
import org.springframework.stereotype.Repository;
import top.kribug.userservice.entity.User;

import java.util.List;

@Mapper
@Repository
public interface UserMapper {

    @Select("SELECT * FROM user")
    List<User> selectAllUser();

    @Select("SELECT * FROM user WHERE id = #{id}")
    User selectById(Integer id);

    @Select("SELECT * FROM user WHERE username = #{username}")
    User selectByUsername(String username);

    @Select("SELECT * FROM user WHERE phone = #{phone}")
    User selectByPhone(String phone);

    @Select("SELECT * FROM user WHERE username = #{username} AND password = #{password}")
    User selectByUsernameAndPassword(User user);

    @Insert("INSERT INTO user (username,password,phone,name,email,headUrl,addTime,state) VALUES " +
            "(#{username},#{password},#{phone},#{name},#{email},#{headUrl},#{addTime},#{state})")
    @Options(useGeneratedKeys = true, keyColumn = "id", keyProperty = "id")
    boolean insert(User user);

    @Delete("DELETE FROM user WHERE id = #{id}")
    boolean delete(User user);

    @Update("UPDATE user SET password = #{password}, phone = #{phone}, name = #{name}, email = #{email}, headUrl = #{headUrl}," +
            "state = #{state} WHERE id = #{id}")
    boolean update(User user);
}
