
 ########################## 合并小时文件 ########################################
 rm(list = ls())
 library(ncdf4)
 library(magrittr)
 
 nc <- nc_open("/data1/jzhang/output/landmask_0.1deg.nc",readunlim = F)
 nc_mask <- ncvar_get(nc, varid = "mask")
 nc_close(nc)
 rm(nc)
 
 in_path <- "/data1/jzhang/datasets/gpm_3imerghh/2001"
 nc_files_all <- list.files(path = in_path, pattern = ".HDF5$", full.names = T)
 
 start_time_all <- seq(as.Date("2001-01-01"), as.Date("2001-12-31"), "day")-1
 first_hour <- seq(from=1,to=(length(start_time_all)*48),by=48)
 
 for (t in 1:length(start_time_all)) {
   start_time <- start_time_all[t]
   nc_files <- nc_files_all[(48*t-47):((48*t-47)+47)]
   tmp_array <- array(data = NA, dim = c(3600,1800,48))
   for (n in 1:48) {
     nc <- nc_open(nc_files[n],readunlim = F)
     tmp_array[,,n] <- t(ncvar_get(nc,"Grid/precipitation")/2)*nc_mask###这里将mm/h转换为mm/0.5h
     nc_lon <- ncvar_get(nc, "Grid/lon")
     nc_lat <- ncvar_get(nc, "Grid/lat")
     nc_close(nc)
     m=nc_files[n]
     message(m)
   }
   message("--------------")
   # 定义nc文件的维度（经度、纬度、时间）
   Latitude <- ncdim_def(name = "latitude", units = "degrees_north", vals = nc_lat)
   Longitude <- ncdim_def(name = "longitude", units = "degrees_east", vals = nc_lon)
   time_units <- paste("hours since", as.character(start_time), "23:30:00")
   Time <- ncdim_def(name = "time", units = time_units, vals = seq(from=0.5,to=24,by=0.5))
   # 定义新nc文件的变量
   new_nc_var <- ncvar_def(name = "hourlyPrecipRate", longname = "0.5hourly Precip Rate",
                           units = "mm/0.5hour", dim = list(Longitude,Latitude,Time), 
                           prec = "float", compression = 3)
   # 创建新的NC文件 并将变量写入NC文件
   start_time <- start_time + 1
   out_filename <- paste("/data1/jzhang/datasets/gpm_3imerghh/2001_0.1deg/",
                         as.character(start_time),".nc",sep = "")
   new_nc_file <- nc_create(filename = out_filename, vars = new_nc_var)
   ncvar_put(nc = new_nc_file, varid = new_nc_var, vals = tmp_array)
   nc_close(new_nc_file)
   
 }



########################## 计算日/夜降雨量 #####################################
rm(list = ls())
library(suncalc)
library(tidyverse)
library(terra)
library(ncdf4)
library(magrittr)
args <- commandArgs(trailingOnly = TRUE)
year <- as.numeric(args)
# year <- 2001
year0 <- year-1
start_time <- as.Date(paste(as.character(year0),"-12-31",sep = ""))
end_time <- as.Date(paste(as.character(year),"-12-31",sep = ""))
sumdays <- as.numeric(end_time-start_time)
for (t in 1:sumdays) {
  input_file <- paste("/data1/jzhang/datasets/gpm_3imerghh/2001_0.1deg/",
                      as.character(start_time+t),".nc",sep="")
  out_filename <- paste("/data1/jzhang/datasets/gpm_3imerghh/2001_0.1deg_output/",
                        as.character(start_time+t),
                        "_light_dark.nc",sep="")
  message(input_file)  
  r <- rast(input_file)
  rdf <- as.data.frame(r, xy=T, na.rm=F)
  rm(r)
  data <- data.frame(date=(start_time+t),lat=rdf$y,lon=rdf$x)
  tmp <- getSunlightTimes(data = data, keep = c("sunrise", "sunset"),tz = "UTC") 
  data <- mutate(data, id = row_number())
  rdf <- mutate(rdf, sunrise=tmp$sunrise, sunset=tmp$sunset, id = row_number()) %>% 
    select(-x,-y)
  rm(tmp)
  vdf <- na.omit(rdf) 
  rm(rdf)
  
  hour_index <- seq(1:48)
  get_light_index <- function(sun_set, sun_ris){
    sunset_index <- round(as.numeric(difftime(sun_set, trunc(sun_set,"days"), units="secs")) / (30*60)) + 1
    sunris_index <- round(as.numeric(difftime(sun_ris, trunc(sun_ris,"days"), units="secs")) / (30*60)) + 1
    light_hour_index0 <- hour_index[hour_index >= sunris_index]
    light_hour_index1 <- hour_index[hour_index < sunset_index]
    ifelse(as.Date(sun_set) == as.Date(sun_ris),
           light_hour_index <- intersect(light_hour_index0, light_hour_index1),
           light_hour_index <- union(light_hour_index0, light_hour_index1))
    return(light_hour_index)
  }
  # light_hour_index <- get_light_index(sun_set, sun_ris)
  # dark_hour_index <- setdiff(hour_index, light_hour_index)
  
  cal_prec_sum <- function(x){
    light_hour_index <- get_light_index(as.POSIXlt(x[50],"UTC"), as.POSIXlt(x[49],"UTC"))
    dark_hour_index <- setdiff(hour_index, light_hour_index)
    x <- as.numeric(x[1:48])
    if (length(light_hour_index)==0) {
      light_sum <- 0
    }else{
      light_sum <- sum(x[light_hour_index],na.rm = T)
    }
    if (length(dark_hour_index)==0) {
      dark_sum <- 0
    }else{
      dark_sum <- sum(x[dark_hour_index],na.rm = T)
    }
    prec <- c(light_sum,dark_sum)
    return(prec)
  }
  
  pre_sum_ris_set <- apply(vdf,1,cal_prec_sum)
  pre_sum_ris_set <- t(pre_sum_ris_set) %>%
    as.data.frame() %>% 
    mutate(id=vdf$id)
  
  merged_df <- left_join(data, pre_sum_ris_set, by = "id")
  rm(pre_sum_ris_set, data, vdf)
  
  light_array <- merged_df[,c(2,3,5)] %>%
    pivot_wider(names_from = lat, values_from = V1) 
  light <- do.call(cbind,light_array)
  
  dark_array <- merged_df[,c(2,3,6)] %>%
    pivot_wider(names_from = lat, values_from = V2) 
  dark <- do.call(cbind,dark_array)
  
  nc_lat <- seq(from=-89.95, to=89.95, by=0.1)
  nc_lon <- seq(from=-179.95, to=179.95, by=0.1)
  
  Latitude <- ncdim_def(name = "latitude", units = "degrees_north", vals = nc_lat)
  Longitude <- ncdim_def(name = "longitude", units = "degrees_east", vals = nc_lon)
  new_nc_var <- ncvar_def(name = "lightHourlyPrecipRate", longname = "hourly Precip Rate in light",
                          units = "mm", dim = list(Longitude,Latitude), 
                          prec = "float", compression = 3)
  new_nc_var2 <- ncvar_def(name = "darkHourlyPrecipRate", longname = "hourly Precip Rate in dark",
                           units = "mm", dim = list(Longitude,Latitude), 
                           prec = "float", compression = 3)
  
  new_nc_file <- nc_create(filename = out_filename, vars = list(new_nc_var,new_nc_var2))
  ncvar_put(nc = new_nc_file, varid = new_nc_var, vals = light[,1801:2])
  ncvar_put(nc = new_nc_file, varid = new_nc_var2, vals = dark[,1801:2])
  nc_close(new_nc_file)
}




##################### 计算日/夜年总降雨量 和 日/夜降水量指数 ###################
rm(list = ls())
library(ncdf4)
library(magrittr)

cal_max_prec_dark <- function(x){
  if (is.na(x[2])) {
    y <- NA
  }else if(x[2]>0.1){
    y <- 1
  }else if(x[2]<=0.1){
    y <- 0
  }
  return(y)
}

cal_max_prec_light <- function(x){
  if (is.na(x[1])) {
    y <- NA
  }else if(x[1]>0.1){
    y <- 1
  }else if(x[1]<=0.1){
    y <- 0
  }
  return(y)
}


nc_files <- list.files(path = "/data1/jzhang/datasets/gpm_3imerghh/2001_0.1deg_output",
                       pattern = ".nc$",full.names = T)
out_filename <- "/data1/jzhang/datasets/gpm_3imerghh/prec_sum_index_2001_0.1deg.nc"
ndays <- length(nc_files)
light_tmp <- array(data = NA, c(3600,1800,ndays))
dark_tmp <- array(data = NA, c(3600,1800,ndays))
light_tmp0 <- array(data = NA, c(3600,1800,ndays))
dark_tmp0 <- array(data = NA, c(3600,1800,ndays))
for (n in 1:ndays) {
  ligth_dark <- array(data=NA,dim = c(3600,1800,2))
  nc <- nc_open(filename = nc_files[n],readunlim = F)
  
  ligth_dark[,,1] <- ncvar_get(nc, varid = "lightHourlyPrecipRate")
  ligth_dark[,,2] <- ncvar_get(nc, varid = "darkHourlyPrecipRate")
  
  light_tmp[,,n] <- apply(ligth_dark, c(1,2), cal_max_prec_light)
  dark_tmp[,,n] <- apply(ligth_dark, c(1,2), cal_max_prec_dark)
  
  light_tmp0[,,n] <- ligth_dark[,,1]
  dark_tmp0[,,n] <- ligth_dark[,,2]
  
  nc_close(nc)
  rm(nc)
}

nc <- nc_open("/data1/jzhang/output/landmask_0.1deg.nc",
              readunlim = F)
nc_mask <- ncvar_get(nc, varid = "mask")
nc_close(nc)
rm(nc)

light_index <- apply(light_tmp,c(1,2),sum,na.rm=T)*nc_mask
dark_index <- apply(dark_tmp,c(1,2),sum,na.rm=T)*nc_mask

light_sum <- apply(light_tmp0,c(1,2),sum,na.rm=T)*nc_mask
dark_sum <- apply(dark_tmp0,c(1,2),sum,na.rm=T)*nc_mask

nc_lat <- seq(from=-89.95, to=89.95, by=0.1)
nc_lon <- seq(from=-179.95, to=179.95, by=0.1)

Latitude <- ncdim_def(name = "latitude", units = "degrees_north", vals = nc_lat)
Longitude <- ncdim_def(name = "longitude", units = "degrees_east", vals = nc_lon)

new_nc_var1 <- ncvar_def(name = "lightIndex", longname = "Precip in light index",
                         units = "-", dim = list(Longitude,Latitude), 
                         prec = "float", compression = 3)
new_nc_var2 <- ncvar_def(name = "darkIndex", longname = "Precip in dark index",
                         units = "-", dim = list(Longitude,Latitude), 
                         prec = "float", compression = 3)
new_nc_var3 <- ncvar_def(name = "lightPrecipRate", longname = "yearly Precip Rate in light",
                         units = "mm", dim = list(Longitude,Latitude), 
                         prec = "float", compression = 3)
new_nc_var4 <- ncvar_def(name = "darkPrecipRate", longname = "yearly Precip Rate in dark",
                         units = "mm", dim = list(Longitude,Latitude), 
                         prec = "float", compression = 3)

new_nc_file <- nc_create(filename = out_filename, 
                         vars = list(new_nc_var1,new_nc_var2,new_nc_var3,new_nc_var4))
ncvar_put(nc = new_nc_file, varid = new_nc_var1, vals = light_index)
ncvar_put(nc = new_nc_file, varid = new_nc_var2, vals = dark_index)
ncvar_put(nc = new_nc_file, varid = new_nc_var3, vals = light_sum)
ncvar_put(nc = new_nc_file, varid = new_nc_var4, vals = dark_sum)

nc_close(new_nc_file)
rm(new_nc_file)

