package top.kribug.deviceservice.server;

import org.springframework.stereotype.Component;

@Component
public class HeartBeatServer {
    public boolean checkIdAndPassword(String id, String password){
        return true;
    }
}
