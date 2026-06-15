import pytest
from app import app, distances


@pytest.fixture(autouse=True)
def clear_distances():
    distances.clear()
    yield
    distances.clear()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- Interface web ---

class TestWebUI:

    def test_page_accueil_affiche_formulaire(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'start_point' in response.data
        assert b'end_point' in response.data

    def test_calcul_valide_affiche_resultat(self, client):
        response = client.post('/', data={'start_point': '0,0', 'end_point': '3,4'})
        assert response.status_code == 200
        assert b'5.0' in response.data

    def test_calcul_point_identique_distance_zero(self, client):
        response = client.post('/', data={'start_point': '2,5', 'end_point': '2,5'})
        assert response.status_code == 200
        assert b'0.0' in response.data

    def test_calcul_coordonnees_negatives(self, client):
        response = client.post('/', data={'start_point': '-1,-1', 'end_point': '2,3'})
        assert response.status_code == 200
        assert b'5.0' in response.data

    def test_format_invalide_affiche_erreur(self, client):
        response = client.post('/', data={'start_point': 'abc,5', 'end_point': '1,2'})
        assert response.status_code == 200
        assert b'invalide' in response.data.lower()
        assert b'5.0' not in response.data

    def test_champ_vide_affiche_erreur(self, client):
        response = client.post('/', data={'start_point': '', 'end_point': '1,2'})
        assert response.status_code == 200
        assert b'invalide' in response.data.lower()

    def test_virgule_manquante_affiche_erreur(self, client):
        response = client.post('/', data={'start_point': '34', 'end_point': '1,2'})
        assert response.status_code == 200
        assert b'invalide' in response.data.lower()

    def test_calcul_valide_sauvegarde_dans_historique(self, client):
        client.post('/', data={'start_point': '0,0', 'end_point': '3,4'})
        assert len(distances) == 1
        assert distances[0]['result_distance'] == 5.0

    def test_erreur_ne_sauvegarde_pas_dans_historique(self, client):
        client.post('/', data={'start_point': 'abc', 'end_point': '1,2'})
        assert len(distances) == 0


# --- API JSON ---

class TestAPI:

    def test_calcul_valide(self, client):
        response = client.post('/api/distance',
                               json={'start_point': '0,0', 'end_point': '3,4'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['result_distance'] == 5.0

    def test_calcul_point_identique_distance_zero(self, client):
        response = client.post('/api/distance',
                               json={'start_point': '2,5', 'end_point': '2,5'})
        assert response.status_code == 200
        assert response.get_json()['result_distance'] == 0.0

    def test_calcul_coordonnees_negatives(self, client):
        response = client.post('/api/distance',
                               json={'start_point': '-1,-1', 'end_point': '2,3'})
        assert response.status_code == 200
        assert response.get_json()['result_distance'] == 5.0

    def test_champ_manquant_start_point(self, client):
        response = client.post('/api/distance', json={'end_point': '3,4'})
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_champ_manquant_end_point(self, client):
        response = client.post('/api/distance', json={'start_point': '0,0'})
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_format_invalide_retourne_400(self, client):
        response = client.post('/api/distance',
                               json={'start_point': 'abc,5', 'end_point': '1,2'})
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_sans_corps_json_retourne_415(self, client):
        response = client.post('/api/distance', data='pas du json',
                               content_type='text/plain')
        assert response.status_code == 415

    def test_calcul_valide_sauvegarde_dans_historique(self, client):
        client.post('/api/distance', json={'start_point': '0,0', 'end_point': '3,4'})
        assert len(distances) == 1

    def test_methode_get_non_autorisee(self, client):
        response = client.get('/api/distance')
        assert response.status_code == 405

    def test_methode_put_non_autorisee(self, client):
        response = client.put('/api/distance', json={'start_point': '0,0', 'end_point': '1,1'})
        assert response.status_code == 405


# --- Historique ---

class TestHistorique:

    def test_historique_vide_au_depart(self, client):
        response = client.get('/api/distances')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_historique_apres_calcul_ui(self, client):
        client.post('/', data={'start_point': '0,0', 'end_point': '3,4'})
        response = client.get('/api/distances')
        assert len(response.get_json()) == 1

    def test_historique_apres_calcul_api(self, client):
        client.post('/api/distance', json={'start_point': '0,0', 'end_point': '3,4'})
        response = client.get('/api/distances')
        assert len(response.get_json()) == 1

    def test_historique_cumule_ui_et_api(self, client):
        client.post('/', data={'start_point': '0,0', 'end_point': '3,4'})
        client.post('/api/distance', json={'start_point': '1,1', 'end_point': '4,5'})
        response = client.get('/api/distances')
        assert len(response.get_json()) == 2
