package top.kribug.deviceservice;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import top.kribug.deviceservice.server.AsrServer;
import top.kribug.deviceservice.server.DataContainer;

import javax.sql.DataSource;

@SpringBootTest
class DeviceServiceApplicationTests {

    @Test
    void contextLoads() {
    }

    @Autowired
    DataContainer dataContainer;
    @Autowired
    DataContainer dataContainer2;

    @Autowired
    DataSource dataSource;
    @Test
    void testDataContainer(){

    }
}
