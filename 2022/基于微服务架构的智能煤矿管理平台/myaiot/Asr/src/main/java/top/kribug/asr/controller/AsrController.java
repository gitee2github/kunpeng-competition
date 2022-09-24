package top.kribug.asr.controller;

import com.baidu.speech.restapi.asrdemo.AsrMain;
import com.baidu.speech.restapi.common.DemoException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import top.kribug.asr.Res;
import top.kribug.asr.feign.FeignDeviceClient;
import top.kribug.asr.result.AsrResult;
import top.kribug.asr.result.Result;

import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.io.InputStream;

@CrossOrigin
@RestController
@RequestMapping("/asr")
public class AsrController {

    private final AsrMain asrMain = new AsrMain();//语音翻译

    @Autowired
    ObjectMapper mapper;

    @Autowired
    FeignDeviceClient deviceClient;

    @PostMapping("/")
    public AsrResult asr(MultipartFile file, HttpSession session){
        if (file == null) return null;
        String res = null;
        InputStream inputStream = null;
        try {
            inputStream = file.getInputStream();
            res = asrMain.start(inputStream);
        } catch (IOException | DemoException e) {
            e.printStackTrace();
        }
        Res res1 = null;
        try {
            res1 = mapper.readValue(res, Res.class);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
        AsrResult asrResult = new AsrResult();
        asrResult.setSpeak(res1.getResult().get(0));


        //处理业务
        String asr = deviceClient.asr(asrResult.getSpeak());
        asrResult.setResult(asr);
        return asrResult;
    }
}
