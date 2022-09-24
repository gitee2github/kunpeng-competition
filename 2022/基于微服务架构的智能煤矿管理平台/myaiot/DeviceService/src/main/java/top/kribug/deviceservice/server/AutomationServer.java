package top.kribug.deviceservice.server;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import top.kribug.deviceservice.entity.*;
import top.kribug.deviceservice.service.*;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Component
public class AutomationServer {

    @Autowired
    private ConditionService conditionService;

    @Autowired
    private AutomationService automationService;

    @Autowired
    private AttributeService attributeService;
    @Autowired
    private DeviceStatusServer deviceStatusServer;

    @Autowired
    private ActionService actionService;

    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    @Autowired
    private OptionService optionService;

    public void dataChangeBack(Integer deviceId){
        Device device = new Device();
        device.setId(deviceId);
        List<Condition> conditions = conditionService.selectByDeviceId(device);

        HashSet<Automation> automationSet = new HashSet<>();
        for (Condition condition : conditions) {
            Automation automation = automationService.selectById(condition.getAutomationId());
            automationSet.add(automation);
        }

        for (Automation automation : automationSet) {
            if(automation.getStatus() != 1){
                continue;
            }
            boolean result = false;
            Integer andCondition = automation.getAndCondition();//执行条件
            List<Condition> conditionsAll = conditionService.selectByAutomationId(automation);
            if(andCondition == 1){
                result = true;
                for (Condition condition : conditionsAll) {
                    Attribute attribute = attributeService.selectById(condition.getAttributeId());
                    Integer deviceId1 = condition.getDeviceId();
                    Device device2 = deviceStatusServer.getDeviceById(deviceId1);
                    if(device2.getInLineState() == 1){
                        String jsonStatusInfo = device2.getJsonStatusInfo();
                        String valueInJsonByKey = getValueInJsonByKey(jsonStatusInfo, attribute.getKey());
                        if(condition.getCompare() == 0){
                            if(!condition.getValue().equals(valueInJsonByKey)){
                                result = false;
                                break;
                            }
                        }else if(condition.getCompare() > 0){
                            Double deviceStatusValue = Double.valueOf(valueInJsonByKey);
                            Double conditionValue = Double.valueOf(condition.getValue());
                            if(conditionValue >= deviceStatusValue) result = false;
                            break;
                        }else{
                            Double deviceStatusValue = Double.valueOf(valueInJsonByKey);
                            Double conditionValue = Double.valueOf(condition.getValue());
                            if(conditionValue <= deviceStatusValue) result = false;
                            break;
                        }
                    }else {
                        result = false;
                    }
                }
                //所有条件满足
            }else{
                for (Condition condition : conditionsAll) {
                    Attribute attribute = attributeService.selectById(condition.getAttributeId());
                    Integer deviceId1 = condition.getDeviceId();
                    Device device2 = deviceStatusServer.getDeviceById(deviceId1);
                    if(device2.getInLineState() == 1){
                        String jsonStatusInfo = device2.getJsonStatusInfo();
                        String valueInJsonByKey = getValueInJsonByKey(jsonStatusInfo, attribute.getKey());
                        if(condition.getCompare() == 0){
                            if(condition.getValue().equals(valueInJsonByKey)){
                                result = true;
                                break;
                            }
                        }else if(condition.getCompare() > 0){
                            Double deviceStatusValue = Double.valueOf(valueInJsonByKey);
                            Double conditionValue = Double.valueOf(condition.getValue());
                            if(conditionValue < deviceStatusValue) result = true;
                            break;
                        }else{
                            Double deviceStatusValue = Double.valueOf(valueInJsonByKey);
                            Double conditionValue = Double.valueOf(condition.getValue());
                            if(conditionValue > deviceStatusValue) result = true;
                            break;
                        }
                    }
                }
            }
            if(result){
                List<Action> actions = actionService.selectByAutomationId(automation);
                System.out.println(actions);
                for (Action action : actions) {
                    Option option = optionService.selectById(action.getOptionId());
                    redisTemplate.opsForValue().set("optionRemote:" + action.getDeviceId(), option.getKey()+":"+option.getValue(), 10, TimeUnit.SECONDS);
                }
            }
        }

    }

    public void dataChange(Integer deviceId){
        Device device = new Device();
        device.setId(deviceId);
        List<Condition> conditions = conditionService.selectByDeviceId(device);
        HashMap<Integer, Automation> automationHashMap = new HashMap<>();
        for (Condition condition : conditions) {
            Automation automation = automationService.selectById(condition.getAutomationId());
            if (!automationHashMap.containsKey(automation.getId())){
                automationHashMap.put(automation.getId(), automation);
            }
        }
        for (Map.Entry<Integer, Automation> automationEntry : automationHashMap.entrySet()) {
            Automation currAutomation = automationEntry.getValue();
            if(currAutomation.getStatus() != 1){
                continue;
            }
            Integer andCondition = currAutomation.getAndCondition();
            List<Condition> currConditions = conditionService.selectByAutomationId(currAutomation);
            if(andCondition == 1){
                boolean res = true;
                for (Condition currCondition : currConditions) {
                    Attribute currAttribute = attributeService.selectById(currCondition.getAttributeId());
                    Integer currDeviceId = currCondition.getDeviceId();
                    Device currDevice = deviceStatusServer.getDeviceById(currDeviceId);
                    if (currDevice.getInLineState() != 1){
                        res = false;
                        break;
                    }
                    String currDeviceJsonStatusInfo = currDevice.getJsonStatusInfo();
                    if(currAttribute.getType().equals("switch")){
                        String valueInJsonByKey = getValueInJsonByKey(currDeviceJsonStatusInfo, currAttribute.getKey());
                        if(!currCondition.getValue().equals(valueInJsonByKey)){
                            res = false;
                            break;
                        }
                    }else{
                        Double deviceValue = Double.valueOf(getValueInJsonByKey(currDeviceJsonStatusInfo, currAttribute.getKey()));
                        Integer compare = currCondition.getCompare();
                        Double settingsValue = Double.valueOf(currCondition.getValue());
                        if(compare == 0){
                            if(Math.abs(deviceValue - settingsValue) > 0.000001){
                                res = false;
                                break;
                            }
                        }else if(compare == -1){
                            if(deviceValue >= settingsValue){
                                res = false;
                                break;
                            }
                        }else{
                            if(deviceValue <= settingsValue){
                                res = false;
                                break;
                            }
                        }
                    }
                }
                if(res){
                    executeAutomationAction(currAutomation);
                }
            }else if (andCondition == 0){
                boolean res = false;
                for (Condition currCondition : currConditions) {
                    Attribute currAttribute = attributeService.selectById(currCondition.getAttributeId());
                    Integer currDeviceId = currCondition.getDeviceId();
                    Device currDevice = deviceStatusServer.getDeviceById(currDeviceId);
                    if (currDevice.getInLineState() != 1){
                        continue;
                    }
                    String currDeviceJsonStatusInfo = currDevice.getJsonStatusInfo();
                    if(currAttribute.getType().equals("switch")){
                        String valueInJsonByKey = getValueInJsonByKey(currDeviceJsonStatusInfo, currAttribute.getKey());
                        if(currCondition.getValue().equals(valueInJsonByKey)){
                            res = true;
                            break;
                        }
                    }else{
                        Double deviceValue = Double.valueOf(getValueInJsonByKey(currDeviceJsonStatusInfo, currAttribute.getKey()));
                        Integer compare = currCondition.getCompare();
                        Double settingsValue = Double.valueOf(currCondition.getValue());
                        if(compare == 0){
                            if(Math.abs(deviceValue - settingsValue) < 0.000001){
                                res = true;
                                break;
                            }
                        }else if(compare == -1){
                            if(deviceValue < settingsValue){
                                res = true;
                                break;
                            }
                        }else{
                            if(deviceValue > settingsValue){
                                res = true;
                                break;
                            }
                        }
                    }
                }
                if(res){
                    executeAutomationAction(currAutomation);
                }
            }
        }


    }

    public void executeAutomationAction(Automation automation){
        List<Action> actions = actionService.selectByAutomationId(automation);
        for (Action action : actions) {
            Option option = optionService.selectById(action.getOptionId());
            redisTemplate.opsForValue().set("optionRemote:" + action.getDeviceId(), option.getKey()+":"+option.getValue(), 10, TimeUnit.SECONDS);
        }
    }

    public static String getValueInJsonByKey(String json, String key){
        if (json == null || key == null) return null;

        int i = json.indexOf(key);
        if(i < 0) return null;
        int j = i + 3 + key.length();
        for( ; j < json.length() ; j++){
            if(json.charAt(j) == '"') break;
        }
        System.out.println(json +" | "+ key + " | " +json.substring(i + 3 + key.length(), j));
        return json.substring(i + 3 + key.length(), j);
    }

    public static String replaceValueInJsonByKey(String json, String key, String newValue){
        if (json == null || key == null || newValue == null) return null;

        int i = json.indexOf(key);
        if(i < 0) return null;
        int j = i + 3 + key.length();
        for( ; j < json.length() ; j++){
            if(json.charAt(j) == '"') break;
        }
        System.out.println(json +" | "+ key + " | " +json.substring(i + 3 + key.length(), j));
        return json.substring(0, i + 3 + key.length()) + newValue + json.substring(j);
    }

    /*public static void main(String[] args) {
        String json = "{\"MY_SWITCH\":\"1\",\"MY_BRIGHTNESS\":\"-1\",\"id\":\"105\",\"password\":\"910652\",\"currentTime\":\"1662135680697\"}";
        String key = "password";
        String newValue = "132b3u1iogbda";
        System.out.println(replaceValueInJsonByKey(json, key, newValue));
    }*/

}
