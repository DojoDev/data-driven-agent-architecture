"""
Script de teste para validar integração API + Agente
Execute este script com a API rodando para testar a integração completa
"""
import requests
import time
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:8000"
API_TOKEN = "test_token_123"

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

def test_api_health():
    """Testa se a API está rodando"""
    print_info("Testando health check da API...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API está rodando! Total de sensores: {data['total_sensors']}")
            return True
        else:
            print_error(f"API retornou status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("API não está rodando! Execute 'python api_server.py' primeiro")
        return False
    except Exception as e:
        print_error(f"Erro ao conectar na API: {e}")
        return False

def test_list_sensors():
    """Testa listagem de sensores"""
    print_info("Testando listagem de sensores...")
    try:
        response = requests.get(
            f"{API_URL}/api/sensors",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Listados {data['total']} sensores com sucesso!")
            for sensor in data['sensors'][:3]:
                print(f"  • {sensor['sensor_id']}: {sensor['sensor_name']}")
            return True
        else:
            print_error(f"Erro ao listar sensores: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def test_consumption_query():
    """Testa consulta de consumo"""
    print_info("Testando consulta de consumo do SENSOR_001...")
    
    periods = ["hora", "dia", "semana"]
    
    for period in periods:
        try:
            response = requests.get(
                f"{API_URL}/api/sensors/SENSOR_001/consumption",
                headers={"Authorization": f"Bearer {API_TOKEN}"},
                params={"period": period},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                consumption = data['data']['consumption_kwh']
                print_success(f"Consumo ({period}): {consumption} kWh")
            else:
                print_error(f"Erro na consulta ({period}): {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Erro: {e}")
            return False
    
    return True

def test_invalid_sensor():
    """Testa comportamento com sensor inválido"""
    print_info("Testando sensor inexistente...")
    try:
        response = requests.get(
            f"{API_URL}/api/sensors/SENSOR_999/consumption",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            params={"period": "hora"},
            timeout=5
        )
        
        if response.status_code == 404:
            print_success("API retornou 404 corretamente para sensor inexistente")
            return True
        else:
            print_error(f"API deveria retornar 404, mas retornou {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def test_invalid_period():
    """Testa comportamento com período inválido"""
    print_info("Testando período inválido...")
    try:
        response = requests.get(
            f"{API_URL}/api/sensors/SENSOR_001/consumption",
            headers={"Authorization": f"Bearer {API_TOKEN}"},
            params={"period": "ano"},
            timeout=5
        )
        
        if response.status_code == 400:
            print_success("API retornou 400 corretamente para período inválido")
            return True
        else:
            print_error(f"API deveria retornar 400, mas retornou {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Erro: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print(f"{Fore.YELLOW}🧪 TESTE DE INTEGRAÇÃO - API + AGENTE{Style.RESET_ALL}")
    print("="*60 + "\n")
    
    tests = [
        ("Health Check", test_api_health),
        ("Listar Sensores", test_list_sensors),
        ("Consultar Consumo", test_consumption_query),
        ("Sensor Inexistente", test_invalid_sensor),
        ("Período Inválido", test_invalid_period),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{Fore.YELLOW}[{test_name}]{Style.RESET_ALL}")
        time.sleep(0.5)
        results.append(test_func())
        time.sleep(0.5)
    
    # Resumo
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"{Fore.GREEN}✓ TODOS OS TESTES PASSARAM ({passed}/{total}){Style.RESET_ALL}")
        print(f"{Fore.GREEN}A API está funcionando corretamente!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Agora você pode executar:{Style.RESET_ALL}")
        print(f"  python main.py")
    else:
        print(f"{Fore.RED}✗ ALGUNS TESTES FALHARAM ({passed}/{total}){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Verifique se a API está rodando corretamente{Style.RESET_ALL}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
