package top.kribug.deviceservice.server;

import org.springframework.stereotype.Component;

import java.util.HashMap;

/*
*
* 数据容器,存放前端请求
*
* */
@Component
public class DataContainer {

    private static HashMap<String, HashMap<String, String>> container;

    static{
        container = new HashMap<String, HashMap<String, String>>();
    }

    public static boolean hasId(String id){
        return container.containsKey(id);
    }

    public static void addData(String id, String key, String value){
        System.out.println("id"+id);
        System.out.println("key"+key);
        System.out.println("value" + value);
        if(hasId(id)){
            if(container.get(id).containsKey(key)){
                container.get(id).replace(key, value);
            }else{
                container.get(id).put(key, value);
            }
        }else{
            container.put(id, new HashMap<String, String>());
            container.get(id).put(key, value);
        }
    }

    public static void clearId(String id){
        container.remove(id);
    }

    public static HashMap<String, String> getData(String id){
        return container.get(id);
    }
}
