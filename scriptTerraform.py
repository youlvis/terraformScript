import os
import copy
import subprocess

os.makedirs('datosTerraform', exist_ok=True)
directorio = os.getcwd()
dirFinal = directorio + "\datosTerraform"
path = "./datosTerraform/"
cmdTerraInit = 'terraform init'
cmdTerraPlan = 'terraform plan'
cmdTerrApply = 'terraform apply'

def ModificarParametro(parametro, modificacion, rutaArchivos, archivosEspecificos, pam):
    if (len(archivosEspecificos) > 0):
        listaArchivos = archivosEspecificos
    else:
        listaArchivos = os.listdir(rutaArchivos)
    ubicacionParametro = -1
    datos = ["", ""]
    # leemos todas las rutas de la carpeta terraform
    for archivo in listaArchivos:
        # leemos archivo por archivo
        with open(rutaArchivos+archivo) as conf:
            lineas = conf.readlines()
            # creamos una copia del archivo para después sobreescribirlo con los cambios
            lineasNuevas = copy.deepcopy(lineas)
            for i in range(0, len(lineas)):  # recorremos la linea
                # buscamos donde se encuentra el parámetro
                if (lineas[i][2:2+len(parametro)] == parametro):
                    # guardamos la ubicacion de la linea donde se encuentra el parámetro
                    ubicacionParametro = i
                    break
        if (ubicacionParametro != -1 and pam):  # verificamos que el parámetro se haya encontrado
            datos = lineas[ubicacionParametro].split(
                "=")  # separamos el string (split =)
            # agregamos la modificación al parámetro
            lineasNuevas[ubicacionParametro] = datos[0] + \
                '= "'+modificacion+'"'+'\n'
            # sobreescribimos el archivo con los datos modificados
            with open(rutaArchivos+archivo, "w") as conf:
                conf.writelines(lineasNuevas)
            ubicacionParametro = -1
        elif (ubicacionParametro != -1):
            datos = lineas[ubicacionParametro].split(
                "=")  # separamos el string (split =)
            lineasNuevas[ubicacionParametro] = datos[0]+'='+datos[1][0:-2] + \
                '-'+modificacion+'"\n'  # agregamos la modificación al parámetro
            # sobreescribimos el archivo con los datos modificados
            with open(rutaArchivos+archivo, "w") as conf:
                conf.writelines(lineasNuevas)
            ubicacionParametro = -1


def buscarRutas(rutaArchivos, palabraClave):
    listaArchivos = os.listdir(rutaArchivos)
    rutas = []
    for archivo in listaArchivos:
        sep = archivo.split('-')
        for uni in sep:
            if (uni == palabraClave):
                rutas.append(archivo)
    return rutas

def terraCmd(cmd):
    try:
        terra = subprocess.run(cmd,
                               shell=True,
                               check=True,
                               cwd=dirFinal,
                               )
    except subprocess.CalledProcessError as err:
        handleErr(cmd, err)

def handleErr(cmd, err):
    print(f"\033[91m{'ERROR: Ocurrió un error con los archivos por favor SOLUCIONAR y dar ENTER para continuar'}\033[00m")
    enter = input()
    terraCmd(cmd)


print(f'\033[93m{"Se creo una carpeta en la misma ubicacion del script con el nombre de --> datosTerraform "}\033[00m')
print(f"\033[92m{'UBICACION: '}\033[00m", dirFinal)

print(
    f"\033[92m{'Escriba el ID del proyecto que desea exportar'}\033[00m")
project = input()

cmdExport = r'gcloud alpha resource-config bulk-export --path="{}" --project={} --resource-format=terraform'.format(
    dirFinal, project)

print(f"\033[93m{'Ejecutando: '}\033[00m", cmdExport)

os.system(cmdExport)

terraCmd('gcloud alpha resource-config terraform init-provider')
print(f'\033[93m{"Se creo archivo main.tf"}\033[00m')

print(f"\033[92m{'Por favor digite el ID del nuevo proyecto'}\033[00m")
idname = input()

print(f"\033[92m{'Agregue terminación del nombre de los bucket'}\033[00m")
nameBucket = input()

rutasStorageBucket = buscarRutas(path, "StorageBucket")
rutasMain = buscarRutas(path, "main")

ModificarParametro("project", idname, path, [], True)
ModificarParametro("name", nameBucket, path, rutasStorageBucket, False)
ModificarParametro("region", 'us-central1', path, rutasMain, True)
ModificarParametro("zone", 'us-central1-c', path, rutasMain, True)

print(f'\033[93m{"EJECUTANDO terraform init"}\033[00m')
terraCmd(cmdTerraInit)
terraCmd('gcloud auth application-default login')
print(f'\033[93m{"Se necesita iniciar sesion para continuar"}\033[00m')
print(f'\033[93m{"Dar teclar ENTER una vez inicie sesion"}\033[00m')
input()
print(f'\033[93m{"EJECUTANDO terraform plan"}\033[00m')
terraCmd(cmdTerraPlan)
print(f'\033[93m{"EJECUTANDO terraform apply"}\033[00m')
terraCmd(cmdTerrApply)
print(f'\033[93m{"LISTOOO! TODO OK"}\033[00m')