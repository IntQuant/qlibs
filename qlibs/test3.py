import resource_loader

# print(resource_loader.get_res_data("shaders/basic_textures_shader.glsh"))

resource_loader.search_locations.append("C:/Users/IQuant/Desktop")

print(resource_loader.get_res_path("test2.mtl"))
