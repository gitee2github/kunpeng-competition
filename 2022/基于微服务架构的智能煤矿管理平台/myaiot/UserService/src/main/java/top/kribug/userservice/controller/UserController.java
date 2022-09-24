package top.kribug.userservice.controller;

import cn.hutool.core.util.IdUtil;
import com.wf.captcha.base.Captcha;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.data.redis.core.RedisTemplate;
import top.kribug.userservice.entity.User;
import top.kribug.userservice.enumclass.LoginCodeEnum;
import top.kribug.userservice.result.Result;
import top.kribug.userservice.result.StatusCode;
import top.kribug.userservice.service.UserService;
import top.kribug.userservice.tools.LoginProperties;

import javax.servlet.http.HttpSession;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/user")
@CrossOrigin
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @PostMapping("/login")
    public Result<User> login(@RequestBody User user, HttpSession session){
        User loginUser = userService.login(user);
        if(loginUser == null){
            return new Result<User>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        //验证码判断
        if(!redisTemplate.opsForValue().get(user.getUuid()).equals(user.getCode())){
            return new Result<User>(StatusCode.VERIFY_CODE_ERROR, null);
        }
        session.setAttribute("loginUser", loginUser);
        return new Result<User>(StatusCode.SUCCESS, loginUser);
    }

    @PostMapping("/register")
    public Result<User> register(@RequestBody User user, HttpSession session){
        //验证码判断
        if(!redisTemplate.opsForValue().get(user.getUuid()).equals(user.getCode())){
            return new Result<User>(StatusCode.VERIFY_CODE_ERROR, null);
        }
        boolean registerCondition = userService.register(user);
        if(registerCondition){
            return new Result<User>(StatusCode.SUCCESS, null);
        }
        return new Result<User>(StatusCode.REQUEST_PARAMETER_ERROR, null);
    }

    @PostMapping("/logout")
    public Result<Boolean> login(HttpSession session){
        session.invalidate();
        return new Result<Boolean>(StatusCode.SUCCESS, true);
    }

    @GetMapping("/getCurrentUser")
    public Result<User> getCurrentUser(HttpSession session){
        User currentUser = (User)session.getAttribute("loginUser");
        if(currentUser == null){
            return new Result<User>(StatusCode.ID_ERROR, null);
        }
        return new Result<User>(StatusCode.SUCCESS, currentUser);
    }

    @GetMapping("/{id}")
    public User getById(@PathVariable Integer id){
        System.out.println(id);
        return userService.selectById(id);
    }

    @GetMapping("/getCurrentUserOnFeign")
    public User getCurrentUserOnFeign(HttpSession session){
        return (User)session.getAttribute("loginUser");
    }

    @GetMapping("/getAll")
    public Result<List<User>> getAll(){
        List<User> users = userService.selectAll();
        return new Result<>(StatusCode.SUCCESS, users);
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Integer id){
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean res = false;
        User user = new User();
        user.setId(id);
        res = userService.delete(user);
        return new Result<>(StatusCode.SUCCESS, res);
    }
    @PostMapping("/")
    public Result<Boolean> addUser(User user){
        if(user == null || user.getUsername() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        if(userService.selectByUsername(user.getUsername()) != null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false, "用户名重复了！");
        }
        if(userService.selectByPhone(user.getPhone()) != null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false, "手机号重复了！");
        }
        boolean res = false;
        res = userService.register(user);
        return new Result<>(StatusCode.SUCCESS, res);
    }

    @PutMapping("/")
    public Result<Boolean> update(User user){
        if(user == null || user.getId() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        if(userService.selectById(user.getId()) == null){
            return new Result<>(StatusCode.ID_ERROR, false, "该用户不存在无法修改");
        }
        boolean res = false;
        res = userService.update(user);
        return new Result<>(StatusCode.SUCCESS, res);
    }

    @PutMapping("/updatePassword")
    public Result<Boolean> updatePassword(User user, String oldPassword){
        if(user == null || user.getId() == null || user.getPassword() == null || user.getPassword().equals("")){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        User user1 = userService.selectById(user.getId());
        if(!user1.getPassword().equals(oldPassword)){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false, "原密码错误");
        }
        user1.setPassword(user.getPassword());
        boolean res = false;
        res = userService.update(user1);
        return new Result<>(StatusCode.SUCCESS, res);
    }


    @GetMapping("/code")
    public Object getCode(){
        LoginProperties loginProperties = new LoginProperties();
        Captcha captcha = loginProperties.getCaptcha();
        String uuid = "code-key-"+ IdUtil.simpleUUID();
        //当验证码类型为 arithmetic时且长度 >= 2 时，captcha.text()的结果有几率为浮点型
        String captchaValue = captcha.text();
        if(captcha.getCharType()-1 == LoginCodeEnum.ARITHMETIC.ordinal() && captchaValue.contains(".")){
            captchaValue = captchaValue.split("\\.")[0];
        }
        // 保存
        redisTemplate.opsForValue().set(uuid,captchaValue,loginProperties.getLoginCode().getExpiration(), TimeUnit.MINUTES);
        // 验证码信息
        Map<String,Object> imgResult = new HashMap<String,Object>(2){{
            put("img",captcha.toBase64());
            put("uuid",uuid);
        }};
        return imgResult;

    }
}
