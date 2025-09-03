use ndarray::{Array2, Array1};
use num_complex::Complex64;
use rand::Rng;

#[derive(Debug)]
pub struct QuantumRegister {
    num_qubits: usize,
    state_vector: Array1<Complex64>,
}

impl QuantumRegister {
    pub fn new(num_qubits: usize) -> Self {
        let size = 1 << num_qubits;
        let mut state_vector = Array1::zeros(size);
        state_vector[0] = Complex64::new(1.0, 0.0);
        
        QuantumRegister {
            num_qubits,
            state_vector,
        }
    }
    
    pub fn hadamard(&mut self, target: usize) {
        let h = Array2::from_shape_vec((2, 2), vec![
            Complex64::new(1.0/2.0_f64.sqrt(), 0.0),
            Complex64::new(1.0/2.0_f64.sqrt(), 0.0),
            Complex64::new(1.0/2.0_f64.sqrt(), 0.0),
            Complex64::new(-1.0/2.0_f64.sqrt(), 0.0),
        ]).unwrap();
        
        self.apply_gate(target, &h);
    }
    
    pub fn cnot(&mut self, control: usize, target: usize) {
        let size = 1 << self.num_qubits;
        let mut new_state = Array1::zeros(size);
        
        for i in 0..size {
            if (i & (1 << control)) != 0 {
                let flipped = i ^ (1 << target);
                new_state[flipped] = self.state_vector[i];
            } else {
                new_state[i] = self.state_vector[i];
            }
        }
        
        self.state_vector = new_state;
    }
    
    pub fn measure(&self) -> Vec<bool> {
        let mut rng = rand::thread_rng();
        let mut result = vec![false; self.num_qubits];
        let random = rng.gen::<f64>();
        
        let mut cumulative = 0.0;
        for (i, amplitude) in self.state_vector.iter().enumerate() {
            cumulative += amplitude.norm_sqr();
            if random < cumulative {
                for j in 0..self.num_qubits {
                    result[j] = (i & (1 << j)) != 0;
                }
                break;
            }
        }
        
        result
    }
    
    fn apply_gate(&mut self, target: usize, gate: &Array2<Complex64>) {
        let size = 1 << self.num_qubits;
        let mut new_state = Array1::zeros(size);
        
        for i in 0..size {
            let bit = (i >> target) & 1;
            let paired_index = i ^ (1 << target);
            
            new_state[i] = 
                gate[[0, bit]] * self.state_vector[i] +
                gate[[1, bit]] * self.state_vector[paired_index];
        }
        
        self.state_vector = new_state;
    }
}

// Quantum cryptography protocol implementation
pub struct BB84Protocol {
    alice_bits: Vec<bool>,
    alice_bases: Vec<bool>,
    bob_bases: Vec<bool>,
    quantum_channel: QuantumRegister,
}

impl BB84Protocol {
    pub fn new(num_bits: usize) -> Self {
        let mut rng = rand::thread_rng();
        
        BB84Protocol {
            alice_bits: (0..num_bits).map(|_| rng.gen()).collect(),
            alice_bases: (0..num_bits).map(|_| rng.gen()).collect(),
            bob_bases: (0..num_bits).map(|_| rng.gen()).collect(),
            quantum_channel: QuantumRegister::new(num_bits),
        }
    }
    
    pub fn generate_key(&mut self) -> Vec<bool> {
        let mut shared_key = Vec::new();
        
        for i in 0..self.alice_bits.len() {
            // Alice prepares qubit
            if self.alice_bases[i] {
                self.quantum_channel.hadamard(i);
            }
            if self.alice_bits[i] {
                self.quantum_channel.cnot(i, i);
            }
            
            // Bob measures
            if self.bob_bases[i] {
                self.quantum_channel.hadamard(i);
            }
            
            let measurement = self.quantum_channel.measure();
            
            // Keep bits where bases match
            if self.alice_bases[i] == self.bob_bases[i] {
                shared_key.push(measurement[i]);
            }
        }
        
        shared_key
    }
}