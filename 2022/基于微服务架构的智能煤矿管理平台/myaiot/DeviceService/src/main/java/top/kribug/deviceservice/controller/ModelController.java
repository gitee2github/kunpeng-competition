package top.kribug.deviceservice.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import top.kribug.deviceservice.entity.Model;
import top.kribug.deviceservice.result.Result;
import top.kribug.deviceservice.result.StatusCode;
import top.kribug.deviceservice.service.ModelService;

import java.util.List;

@RestController
@RequestMapping("/device/model")
@CrossOrigin
public class ModelController {

    @Autowired
    private ModelService modelService;

    @GetMapping("/getById")
    public Result<Model> getById(Model model){
        if (model == null || model.getId() == null){
            return new Result<Model>(StatusCode.REQUEST_PARAMETER_ERROR, null);
        }
        Model model1 = modelService.selectById(model.getId());
        return new Result<Model>(StatusCode.SUCCESS, model1);
    }

    @GetMapping("/getAll")
    public Result<List<Model>> getAll(){
        List<Model> models = modelService.selectAllModel();
        return new Result<>(StatusCode.SUCCESS, models);
    }

    @PostMapping("/")
    public Result<Boolean> add(Model model){
        if(model == null || model.getTitle() == null || model.getServerName() == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        boolean insert = modelService.insert(model);
        if(insert){
            return new Result<>(StatusCode.SUCCESS, true);
        }
        return new Result<>(StatusCode.SQL_ERROR, false);

    }

    @DeleteMapping("/{id}")
    public Result<Boolean> add(@PathVariable Integer id) {
        if(id == null){
            return new Result<>(StatusCode.REQUEST_PARAMETER_ERROR, false);
        }
        Model model = new Model();
        model.setId(id);
        boolean res = modelService.delete(model);
        if(res){
            return new Result<>(StatusCode.SUCCESS, true);
        }
        return new Result<>(StatusCode.SQL_ERROR, false);

    }
}
