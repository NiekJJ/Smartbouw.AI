<template>
  <div class="p-6">
    <h2>📋 Klantenoverzicht</h2>

    <form @submit.prevent="submitForm" class="mb-4 space-y-2">
      <div><input v-model="form.voornaam" placeholder="Voornaam" required /></div>
      <div><input v-model="form.achternaam" placeholder="Achternaam" required /></div>
      <div><input v-model="form.straatnaam" placeholder="Straatnaam" /></div>
      <div><input v-model="form.huisnummer" placeholder="Huisnummer" /></div>
      <div><input v-model="form.postcode" placeholder="Postcode" /></div>
      <div><input v-model="form.woonplaats" placeholder="Woonplaats" /></div>
      <div><input v-model="form.email" type="email" placeholder="E-mailadres" /></div>
      <div><input v-model="form.telefoon" placeholder="Telefoonnummer" /></div>
      <div><input v-model="form.klantnummer" placeholder="Klantnummer (bv. KLT-0001)" /></div>
      <div>
        <select v-model="form.klanttype">
          <option disabled value="">-- Kies klanttype --</option>
          <option value="particulier">Particulier</option>
          <option value="zakelijk">Zakelijk</option>
          <option value="leverancier">Leverancier</option>
        </select>
      </div>
      <button type="submit">
        {{ bewerkModus ? "💾 Klant bijwerken" : "➕ Klant toevoegen" }}
      </button>
      <button type="button" v-if="bewerkModus" @click="annuleerBewerken">Annuleren</button>
    </form>

    <div v-if="klanten.length">
      <h3>📄 Geregistreerde klanten:</h3>
      <ul>
        <li v-for="klant in klanten" :key="klant.id">
          <strong>{{ klant.voornaam }} {{ klant.achternaam }}</strong> – {{ klant.email }}  
          <button @click="vulFormulier(klant)">✏️</button>
          <button @click="verwijderKlant(klant.id)">🗑️</button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "KlantenOverzicht",
  data() {
    return {
      klanten: [],
      form: {
        voornaam: "",
        achternaam: "",
        straatnaam: "",
        huisnummer: "",
        postcode: "",
        woonplaats: "",
        email: "",
        telefoon: "",
        klantnummer: "",
        klanttype: ""
      },
      bewerkModus: false,
      actieveKlantId: null
    };
  },
  methods: {
    async getKlanten() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/klanten");
        this.klanten = res.data;
      } catch (err) {
        alert("❌ Fout bij ophalen klanten");
        console.error(err);
      }
    },
    async submitForm() {
      try {
        if (this.bewerkModus) {
          await axios.put(`http://127.0.0.1:8000/klanten/${this.actieveKlantId}`, this.form);
          alert("✅ Klant bijgewerkt!");
        } else {
          await axios.post("http://127.0.0.1:8000/klanten", this.form);
          alert("✅ Klant toegevoegd!");
        }
        this.resetForm();
        this.getKlanten();
      } catch (err) {
        alert("❌ Fout: " + (err.response?.data?.detail || "onbekend"));
      }
    },
    vulFormulier(klant) {
      this.form = { ...klant };
      this.bewerkModus = true;
      this.actieveKlantId = klant.id;
    },
    annuleerBewerken() {
      this.resetForm();
    },
    resetForm() {
      this.form = {
        voornaam: "",
        achternaam: "",
        straatnaam: "",
        huisnummer: "",
        postcode: "",
        woonplaats: "",
        email: "",
        telefoon: "",
        klantnummer: "",
        klanttype: ""
      };
      this.bewerkModus = false;
      this.actieveKlantId = null;
    },
    async verwijderKlant(id) {
      if (!confirm("Weet je zeker dat je deze klant wilt verwijderen?")) return;
      try {
        await axios.delete(`http://127.0.0.1:8000/klanten/${id}`);
        alert("🗑️ Klant verwijderd!");
        this.getKlanten();
      } catch (err) {
        alert("❌ Fout bij verwijderen klant");
        console.error(err);
      }
    }
  },
  mounted() {
    this.getKlanten();
  }
};
</script>
